import Chart from "react-apexcharts";
import { SacDmProps } from "../../SacDm/types";
import { EmptyData } from "../../../components/EmptyData";
import React, { useCallback, useEffect, useState } from "react";
import { SacDmDefaultProps } from "../../../types";
import sacDmDefault from "../../../app/services/sacdm_default";
import {Divider, Section, containerStyle, statusBoxStyle, statusOkStyle, statusFailStyle,} from "../styles"

export const SacDmDevice = ({
  deviceId,
  sacDm,
}: {
  deviceId: number ;
  sacDm: SacDmProps[];
}) => {
  const [sacDmMean, setsacDmMean] = useState<SacDmDefaultProps>();

  const loadSacDmDefault = useCallback(async () => {
    try {
      const response = await sacDmDefault.getSacDmDefault(deviceId);
      setsacDmMean(response);
      
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    loadSacDmDefault();
  }, [loadSacDmDefault]);

  if (!deviceId) {
    return null;
  }

  // TODO fazer a leitura correta dos dados do status
  // Função para verificar o status dos dados com base em sacDmMean.status
  const checkDataStatus = () => {
    //return sacDmMean?.status === "Ok" ? "Ok" : "Falha";
    return "Falha"
  };

  const optionsChart = {
    chart: {
      id: "device-metrics",
    },
    xaxis: {
      categories: sacDm.map((item: SacDmProps) => item.timestamp),
      labels: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
        style: {
          colors: ["#E0E0E0"],
        },
      },
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
      },
    },
    legend: {
      labels: {
        colors: ["E0E0E0", "E0E0E0", "E0E0E0", "E0E0E0"],
      },
    },
  };

  const getChartData = (axis: "x" | "y" | "z") => {
    const values = sacDm.map((item) =>
      parseFloat(item[`${axis}_value`].toFixed(8))
    );
    const means = Array(sacDm.length).fill(sacDmMean?.[`${axis}_mean`] ?? 0);
    const upperStandardDeviation = sacDmMean
      ? Array(sacDm.length).fill(
          sacDmMean[`${axis}_mean`] + sacDmMean[`${axis}_standard_deviation`]
        )
      : [];
    const lowerStandardDeviation = sacDmMean
      ? Array(sacDm.length).fill(
          sacDmMean[`${axis}_mean`] - sacDmMean[`${axis}_standard_deviation`]
        )
      : [];

    return [
      { name: "Valor", data: values },
      { name: "Média", data: means },
      { name: "Desvio Padrão Superior", data: upperStandardDeviation },
      { name: "Desvio Padrão Inferior", data: lowerStandardDeviation },
    ];
  };

  const dataX = getChartData("x");
  const dataY = getChartData("y");
  const dataZ = getChartData("z");
  const status = checkDataStatus() === "Ok" ? statusOkStyle : statusFailStyle;

  return (
    
    <div style={containerStyle}>
      {/* Retângulo com status de dados */}
      <div style={{ ...statusBoxStyle, ...status }}>
        {checkDataStatus()}
      </div>


      {/* Gráficos para os eixos X, Y e Z */}
      <Section>
        <h3>Eixo X</h3>
        <Chart options={optionsChart} series={dataX} type="line" height="350" />
        <Divider />
      </Section>

      <Section>
        <h3>Eixo Y</h3>
        <Chart options={optionsChart} series={dataY} type="line" height="350" />
        <Divider />
      </Section>

      <Section>
        <h3>Eixo Z</h3>
        <Chart options={optionsChart} series={dataZ} type="line" height="350" />
        <Divider />
      </Section>

      {sacDm.length === 0 && (
        <EmptyData message="Nenhum dado encontrado para o dispositivo selecionado" />
      )}
    </div>
  );
};

export default React.memo(SacDmDevice, (prevProps, nextProps) => {
  return (
    prevProps.deviceId === nextProps.deviceId &&
    JSON.stringify(prevProps.sacDm) === JSON.stringify(nextProps.sacDm)
  );
});
